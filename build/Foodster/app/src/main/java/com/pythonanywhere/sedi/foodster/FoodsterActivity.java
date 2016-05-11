package com.pythonanywhere.sedi.foodster;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.support.design.widget.TabLayout;
import android.support.v4.view.ViewPager;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Toast;

import com.google.zxing.integration.android.IntentIntegrator;
import com.google.zxing.integration.android.IntentResult;
import com.pythonanywhere.sedi.foodster.fragments.BarcodeReaderFragment;
import com.pythonanywhere.sedi.foodster.fragments.RecipesFragment;
import com.pythonanywhere.sedi.foodster.fragments.ShoppingListFragment;
import com.pythonanywhere.sedi.foodster.views.adapters.FoodsterPagerAdapter;

public class FoodsterActivity extends AppCompatActivity {

    private FoodsterPagerAdapter foodsterPagerAdapter;
    private Toolbar toolbar;
    private TabLayout tabLayout;
    private ViewPager viewPager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        if(!checkLogin()){
            finish();
        }

        setContentView(R.layout.activity_main);

        toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        viewPager = (ViewPager) findViewById(R.id.pager);
        setupViewPager(viewPager);

        tabLayout = (TabLayout) findViewById(R.id.tab_layout);
        tabLayout.setupWithViewPager(viewPager);

    }

    private boolean checkLogin(){

        boolean flag = false;

        SharedPreferences sharedPref
                = getSharedPreferences(getString(R.string.token_file_key), Context.MODE_PRIVATE);
        String token
                = sharedPref.getString(getString(R.string.saved_token), getString(R.string.not_logged_status));

        if(token.equals(getString(R.string.not_logged_status))){
            Intent i = new Intent(this, LoginActivity.class);
            startActivity(i);
            flag = false;
        }
        else flag = true;
        return flag;
    }

    private void setupViewPager(ViewPager viewPager){
        foodsterPagerAdapter = new FoodsterPagerAdapter(getSupportFragmentManager());
        foodsterPagerAdapter.addFragment(new ShoppingListFragment(), "Shopping list");
        foodsterPagerAdapter.addFragment(new RecipesFragment(), "Recipes");
        foodsterPagerAdapter.addFragment(new BarcodeReaderFragment(), "Barcode reader");

        viewPager.setAdapter(foodsterPagerAdapter);

    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.log_out) {

            SharedPreferences sharedPref
                    = getSharedPreferences(getString(R.string.token_file_key), Context.MODE_PRIVATE);
            SharedPreferences.Editor editor = sharedPref.edit();
            editor.putString(getString(R.string.saved_token), getString(R.string.not_logged_status));
            editor.commit();

            Intent i = new Intent(this, LoginActivity.class);
            startActivity(i);
            finish();

            return true;
        }

        return super.onOptionsItemSelected(item);
    }

//    public void onActivityResult(int requestCode, int resultCode, Intent intent){
//
//        IntentResult scanningResult = IntentIntegrator.parseActivityResult(requestCode, resultCode, intent);
//
//        if(scanningResult != null){
//            String scanContent = scanningResult.getContents();
//            String scanFormat = scanningResult.getFormatName();
//            Toast toast = Toast.makeText(getApplicationContext(),
//                    "Scan format: " + scanFormat + " ; Scan result: " + scanContent , Toast.LENGTH_LONG);
//            toast.show();
//        }
//    }
}
